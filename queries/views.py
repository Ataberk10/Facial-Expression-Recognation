from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login  # To log the user in after signup
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, QueryCreateForm
from .models import FacialExpressionQuery
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.urls import reverse_lazy  # Useful for success URLs  # noqa: F401
from django.contrib import messages  # Import the messages framework
import os
from .analysis import analyze_facial_expression


# Create your views here.
def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # Creates and saves the new user
            login(request, user)  # Log the user in automatically
            return redirect("home")  # Redirect to the home page after successful signup
    else:  # If it's a GET request, just display a blank form
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


def home(request):
    # Later, this could be a welcome page or redirect to the dashboard if logged in
    return render(request, "home.html")


@login_required  # Ensures only logged-in users can access this view
def query_create(request):
    if request.method == "POST":
        # Pass request.POST (text data) and request.FILES (file data) to the form
        form = QueryCreateForm(request.POST, request.FILES)
        if form.is_valid():
            # Create the object but don't save to DB yet
            query_instance = form.save(commit=False)
            # Assign the current logged-in user
            query_instance.user = request.user

            expression_result = None
            confidence_result = None
            analysis_success = False
            try:
                # Ensure the file is saved to disk before getting the path
                # This happens implicitly with commit=False + accessing field,
                # but let's save temporarily to be absolutely sure path exists
                # (This step might be redundant depending on storage, but safe)
                query_instance.save()  # Save to get ID and ensure file exists on disk

                if query_instance.uploaded_photo:
                    image_path = (
                        query_instance.uploaded_photo.path
                    )  # Get path AFTER saving
                    print(
                        f"Calling analysis function for image: {image_path}"
                    )  # Debug print
                    expression_result, confidence_result = analyze_facial_expression(
                        image_path
                    )

                    if expression_result is not None:
                        query_instance.detected_expression = expression_result
                        query_instance.confidence_score = confidence_result
                        analysis_success = True
                    else:
                        messages.error(
                            request,
                            "Facial expression analysis failed. Please check the logs or try a different image.",
                        )
                        query_instance.detected_expression = (
                            "Analysis Failed"  # Set status
                        )
                        query_instance.confidence_score = None
                else:
                    messages.error(request, "No photo uploaded for analysis.")
                    query_instance.detected_expression = "No Photo"
                    query_instance.confidence_score = None

            except Exception as e:
                # Catch errors getting path or during analysis call
                messages.error(request, f"An error occurred during analysis setup: {e}")
                print(f"Error in view before/during analysis call: {e}")
                import traceback

                traceback.print_exc()
                query_instance.detected_expression = "Error"
                query_instance.confidence_score = None

            # Now save the object with user and analysis result (or placeholder)
            query_instance.save()

            # Redirect based on success
            if analysis_success:
                # Redirect to the detail page for the newly created query
                messages.success(
                    request,
                    f"Query '{query_instance.subject_name}' created and analyzed successfully!",
                )
                return redirect("query_detail", pk=query_instance.pk)
            else:
                # If analysis failed, maybe redirect back to list or stay on detail page (which will show failure status)
                # Redirecting to detail page allows user to see the "Analysis Failed" status.
                return redirect(
                    "query_detail", pk=query_instance.pk
                )  # Redirect even on failure

        else:  # Form is not valid
            # Re-render the form with errors
            pass  # No change needed here, template renders errors automatically
    else:  # If it's a GET request
        form = QueryCreateForm()  # Create an empty form instance

    # Render the template with the form
    return render(request, "queries/query_form.html", {"form": form})


@login_required  # Ensure only logged-in users can see their queries
def query_list(request):
    # Filter queries to get only those belonging to the current user
    user_queries_list = FacialExpressionQuery.objects.filter(
        user=request.user
    ).order_by("-created_at")  # Order by newest first

    # --- Pagination (FR006) ---
    # Show 10 queries per page (adjust as needed)
    paginator = Paginator(user_queries_list, 10)
    page_number = request.GET.get(
        "page"
    )  # Get the page number from URL query param (?page=...)

    try:
        # Get the specific page object
        queries_page = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queries_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queries_page = paginator.page(paginator.num_pages)
    # --- End Pagination ---

    # Pass the paginated queries (or the full list if not using pagination) to the template
    context = {
        "queries_page": queries_page  # Pass the Page object
    }
    return render(request, "queries/query_list.html", context)


@login_required
def query_detail(request, pk):
    # Get the specific query object by its primary key (pk)
    # Also ensure the query belongs to the currently logged-in user
    try:
        query = FacialExpressionQuery.objects.get(pk=pk, user=request.user)
    except FacialExpressionQuery.DoesNotExist:
        # If the query doesn't exist OR doesn't belong to the user, raise a 404 error
        raise Http404("Query not found or you do not have permission to view it.")

    # Alternatively, using get_object_or_404 (more concise):
    # query = get_object_or_404(FacialExpressionQuery, pk=pk, user=request.user)

    context = {"query": query}
    return render(request, "queries/query_detail.html", context)


@login_required
def query_delete(request, pk):
    # Get the query object, ensuring it belongs to the current user
    query = get_object_or_404(FacialExpressionQuery, pk=pk, user=request.user)

    if request.method == "POST":
        # If the form (confirmation) has been submitted
        subject_name = query.subject_name  # Store name before deleting for message
        file_path = None

        # --- Step 1: Get the file path BEFORE deleting the model instance ---
        if query.uploaded_photo:
            # Get the absolute path to the file on the filesystem
            try:
                # This works reliably with default FileSystemStorage
                file_path = query.uploaded_photo.path
            except NotImplementedError:
                # Some storage backends might not implement .path
                # You might need storage-specific methods if not using default storage
                messages.error(
                    request, "Cannot determine file path for automatic deletion."
                )
                # Optionally prevent deletion here if file cleanup is critical
                # return redirect('query_detail', pk=query.pk)

        # --- Step 2: Delete the database record ---
        try:
            query.delete()  # Delete the object from the database
            db_deleted = True
        except Exception as e:
            # Handle potential DB deletion errors
            messages.error(request, f"Database error deleting query: {e}")
            db_deleted = False
            # Redirect back, maybe to detail page or list page
            return redirect("query_detail", pk=pk)  # Or 'query_list'

        # --- Step 3: If DB deletion succeeded and we have a file path, delete the file ---
        file_deleted_successfully = True  # Assume success unless proven otherwise
        if db_deleted and file_path:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    # Optional: Log successful file deletion
                # else: file was already gone, which is fine.
            except OSError as e:
                # Log the error (using print for simplicity, use logging in production)
                print(f"Error deleting file {file_path}: {e}")
                messages.warning(
                    request,
                    f'Query "{subject_name}" deleted, but the associated image file could not be removed due to an error. Please check server logs or permissions.',
                )
                file_deleted_successfully = False
            except Exception as e:
                # Catch any other unexpected errors during file deletion
                print(f"Unexpected error deleting file {file_path}: {e}")
                messages.warning(
                    request,
                    f'Query "{subject_name}" deleted, but the associated image file could not be removed due to an unexpected error.',
                )
                file_deleted_successfully = False

        # --- Step 4: Provide feedback message ---
        if db_deleted and file_deleted_successfully:
            messages.success(
                request,
                f'Query "{subject_name}" and its associated image deleted successfully.',
            )
        # (Warning message is already added above if file deletion failed)

        # --- Step 5: Redirect ---
        return redirect("query_list")

    else:  # GET request
        context = {"query": query}
        return render(request, "queries/query_confirm_delete.html", context)

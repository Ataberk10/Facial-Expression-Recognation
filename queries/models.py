# queries/models.py
from django.db import models
from django.conf import settings  # To reference the User model
import os  # Needed for custom upload path


# Define a function to create a user-specific upload path
def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    # Example: MEDIA_ROOT/user_1/profile.jpg
    return "user_{0}/{1}".format(instance.user.id, filename)


class FacialExpressionQuery(models.Model):
    """
    Represents a single facial expression analysis query.
    """

    # Link to the user who created this query (FR001)
    # settings.AUTH_USER_MODEL refers to Django's built-in User model.
    # on_delete=models.CASCADE means if the user is deleted, their queries are also deleted.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="queries",  # Allows accessing user.queries
    )

    # Subject Name (FR004 - Required)
    subject_name = models.CharField(max_length=100, blank=False, null=False)

    # Uploaded face photo (FR003)
    # 'upload_to' specifies the subdirectory within MEDIA_ROOT
    # We use our custom function here for user-specific folders (FR011)
    uploaded_photo = models.ImageField(
        upload_to=user_directory_path, blank=False, null=False
    )

    # Optional notes (FR004 - Optional)
    notes = models.TextField(blank=True, null=True)

    # Detected expression (FR005)
    # We'll store this as a string. You might refine this later (e.g., choices).
    detected_expression = models.CharField(
        max_length=50, blank=True, null=True
    )  # Allow blank initially

    # Confidence score (FR007 - Optional extension)
    # We can add this later if your model provides it.
    confidence_score = models.FloatField(blank=True, null=True)

    # Timestamps (Good practice)
    created_at = models.DateTimeField(
        auto_now_add=True
    )  # Automatically set when created
    updated_at = models.DateTimeField(auto_now=True)  # Automatically set when saved

    def __str__(self):
        # How the object is represented as a string (e.g., in the admin)
        return f"Query by {self.user.username} for {self.subject_name} ({self.created_at.strftime('%Y-%m-%d')})"

    # Optional: Method to get the filename for display
    def filename(self):
        return os.path.basename(self.uploaded_photo.name)

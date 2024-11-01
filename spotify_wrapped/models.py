from django.db import models

class Feedback(models.Model):
    """
    Model to store user feedback submitted through the 'Contact the Developers' form.

    Attributes:
        name (CharField): The name of the user submitting feedback.
        email (EmailField): The email address of the user submitting feedback.
        message (TextField): The feedback message provided by the user.
        submitted (DateTimeField): The date and time when the feedback was submitted. Auto-generated at creation.
    """
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        String representation of the Feedback object.

        Returns:
            str: Feedback summary, including the name and email of the user.
        """
        return f"Feedback from {self.name} ({self.email}) : {self.message}"
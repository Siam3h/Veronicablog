from django.db import models


class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    pdf = models.FileField(upload_to='projects/pdfs/')
    author = models.CharField(max_length=255)
    
    @property
    def get_image_url(self):
        return self.pdf.url

    def __str__(self):
        return self.title    

class Transaction(models.Model):
    name = models.CharField(max_length=50, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    ref = models.CharField(max_length=200, blank=True)  
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Transaction for {self.project.title} by {self.email}"

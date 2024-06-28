from django.shortcuts import render, HttpResponse
import os
import mimetypes
from django.conf import settings

def download(request, file):
    fl_path = os.path.join(settings.MEDIA_ROOT, file)

    print("Full file path:", fl_path)  # Debugging: Check the constructed file path

    # Open the file in binary read mode
    try:
        with open(fl_path, 'rb') as fl:
            mime_type, _ = mimetypes.guess_type(fl_path)
            response = HttpResponse(fl, content_type=mime_type)
            response['Content-Disposition'] = f"attachment; filename={os.path.basename(file)}"
            return response
    except FileNotFoundError:
        return HttpResponse("File not found.", status=404)

def delete(request, claim_id):
    pass


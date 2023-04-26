import json
from PIL import Image
from io import BytesIO
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

def get_auth_headers(client, user):
        """
        A function to get authentiation headers.
        """ 
        auth_endpoint = reverse('token_obtain_pair')

        auth_credentials = {
            'email_address': user.email_address,
            'password': 'testpassword'
        }
    
        auth_response = client.post(auth_endpoint, auth_credentials)

        auth_headers = {'HTTP_AUTHORIZATION':f'Bearer {json.loads(auth_response.content)["access"]}'}

        return auth_headers

def create_temp_image(filename = 'file'):
    """
    A function to create a temporary in memory image file.
    """
    bts = BytesIO()
    img = Image.new('RGB', (100, 100))
    img.save(bts, 'jpeg')

    temp_file = SimpleUploadedFile(f'{filename}.jpg', bts.getvalue(), content_type='image/jpg')

    return temp_file
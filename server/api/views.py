from django.http.response import HttpResponse
from django.shortcuts import render
import json
import urllib.request
import turicreate as tc
import base64
from PIL import Image
from io import BytesIO

#To load existing model
model = tc.load_model('/home/vignesh/Projects/Image-Similarity-Model/caltech-101.model')

# Load images from the Caltech 101 dataset
reference_data  = tc.image_analysis.load_images('/home/vignesh/Projects/Image-Similarity-Model/101_ObjectCategories')
reference_data = reference_data.add_row_number()

# Create your views here.
def search(request):

    if request.method == "POST":
        try:
            payload = json.loads(request.body)
            image_url = payload['url']
            top_K = payload['k']
        except:
            # Sending response
            response = json.dumps([{"Status":"Failed","Cause":"Wrong API Format"}])
            return HttpResponse(response,content_type='text/json')  

        try:
            # setting filename and image URL
            filename = '/home/vignesh/Projects/Temp/Target_Image.jpg'

            # calling urlretrieve function to get resource
            urllib.request.urlretrieve(image_url, filename)
        except:
            # Sending response
            response = json.dumps([{"Status":"Failed","Cause":"Image Download Faied"}])
            return HttpResponse(response,content_type='text/json')
        
        try:
                # calling image-search function
                return image_search(top_K)
        except Exception as e:
            print(e)
            # Sending response
            response = json.dumps([{"Status":"Failed","Cause":"Image Search Faied"}])
            return HttpResponse(response,content_type='text/json')    

def image_search(top_K):

    # Quering for top k similar images (custom images)
    query_results = model.query(tc.Image('/home/vignesh/Projects/Temp/Target_Image.jpg'), k=top_K)
    
    # Retrive Image paths
    image_paths = reference_data.filter_by(query_results['reference_label'], 'id')["path"]
    
    # Encoding Images using 'Base64' and decode it in 'ASCII' for send in json
    jsonData = [{"Status":"Success","Images":[]}]
    for image_path in image_paths:
        with open(image_path, "rb") as image_file:
            encoded_data = base64.b64encode(image_file.read()).decode("ascii")
        jsonData[0]["Images"].append(encoded_data)

    # Sending response
    response = json.dumps(jsonData)
    return HttpResponse(response,content_type='text/json')
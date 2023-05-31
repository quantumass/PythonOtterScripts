import os
import time
import subprocess
from pocketbase import PocketBase
from pocketbase.client import FileUpload
from PIL import Image

client = PocketBase('http://127.0.0.1:8090')
admin_data = client.admins.auth_with_password("python@imgotter.com", "LPLpcPFpUHd8p!4")
print("authenticated successfuly the admin")
folder_to_watch = os.path.abspath(__file__) + "/../../go/pb_data/storage/c83ukhcc0l9jq90/"
print("started to watch " + folder_to_watch)

while True:
    print("searching ...")
    for root, dirs, files in os.walk(folder_to_watch):
        dirs[:] = [d for d in dirs if not d.startswith("thumbs_")]
        for file in files:
            if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".webp"):
                if not file.endswith("_scaled.png"):    
                    file_path = os.path.join(root, file)
                    processed_file_path = os.path.join(root, "folder.processed")
                    processing_file_path = os.path.join(root, "folder.processing")
                    if not os.path.exists(processed_file_path) and not os.path.exists(processing_file_path):
                        
                        print("found file to be processed")
                        open(processing_file_path, 'a').close()

                        client.collection("images").update(os.path.basename(root), {
                            "isReady": False,
                            "isProcessing": True
                        });

                        # execute script on file_path
                        output_file = os.path.splitext(file)[0] + '_scaled.png'
                        output_path = os.path.join(root, output_file)
                        # subprocess.call(["./scripts/realesrgan-ncnn-vulkan.exe", "-i", file_path, "-o", output_path])
                        subprocess.call(["rembg", "i", file_path, output_path])
                        os.remove(processing_file_path)
                        open(processed_file_path, 'a').close()
                        # print the name of the folder that contains the file
                        # print("File", file, "has been processed in the folder:", )
                        image = Image.open(output_path)
                        image.save(output_path, optimize=True, quality=85)
                        image.close()
                        
                        client.collection("images").update(os.path.basename(root), {
                            "isReady": True,
                            "isProcessing": True,
                            "convertedImage": FileUpload((output_file, open(output_path, "rb")))
                        });

                        image = client.collection("images").get_one(os.path.basename(root))

                        if image.user != Null:
                            user = client.collection("users").get_one(image.user)
                        
                            client.collection("users").update(image.user, {
                                "credits": user.credits - 1
                            });
                        # try:
                        #     os.remove(output_path)
                        #     print(f"File '{output_path}' was deleted successfully.")
                        # except FileNotFoundError:
                        #     print(f"File '{output_path}' not found.")
    time.sleep(10)
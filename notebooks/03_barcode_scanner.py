import cv2
from pyzbar.pyzbar import decode
import requests

cap = cv2.VideoCapture(0)

detected_codes = set()

while True:

    isTrue, frame = cap.read()

    if not isTrue:
        break

    barcodes = decode(frame)

    for barcode in barcodes:

        barcode_data = barcode.data.decode("utf-8")

        x, y, w, h = barcode.rect

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)

        cv2.putText(frame, barcode_data, (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        
        if barcode_data not in detected_codes:

            detected_codes.add(barcode_data)

            print("\n==============================")
            print("Barcode:", barcode_data)

            url = f"https://world.openfoodfacts.org/api/v0/product/{barcode_data}.json"

            response = requests.get(url)

            data = response.json()

            if data["status"] == 1:

                product = data["product"]

                name = product.get("product_name", "Unknown")

                nutriments = product.get("nutriments", {})

                calories = nutriments.get("energy-kcal_100g", "N/A")
                protein = nutriments.get("proteins_100g", "N/A")
                carbs = nutriments.get("carbohydrates_100g", "N/A")
                fat = nutriments.get("fat_100g", "N/A")

                serving_size = product.get("serving_size", "N/A")

                ingredients = product.get("ingredients_text", "N/A")

                print("Product:", name)
                print("Calories (per 100g):", calories)
                print("Protein (per 100g):", protein)
                print("Carbs (per 100g):", carbs)
                print("Fat (per 100g):", fat)
                print("Serving Size:", serving_size)
                print("Ingredients:", ingredients)

            else:
                print("Product not found")

            print("==============================")

    cv2.imshow("NutriLens Barcode Scanner", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
cv2.destroyAllWindows()
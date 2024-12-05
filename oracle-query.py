import requests
import json
from typing import Optional, Dict

class HouseValueEstimator:
    def __init__(self, api_key: str):
        """
        Initialize the house value estimator with an API key.
        
        :param api_key: API key for the property valuation service
        """
        self.api_key = api_key
        self.base_url = "https://api.property-valuation-service.com/v1/estimate"

    def get_house_value(self, 
                        address: str, 
                        zip_code: str, 
                        property_type: str = "single_family") -> Optional[Dict]:
        """
        Retrieve estimated property value from API.
        
        :param address: Street address of the property
        :param zip_code: ZIP code of the property
        :param property_type: Type of property (default: single_family)
        :return: Dictionary containing valuation details or None if API call fails
        """
        # Prepare request payload
        payload = {
            "api_key": self.api_key,
            "address": address,
            "zip_code": zip_code,
            "property_type": property_type
        }

        try:
            # Make API request
            response = requests.post(
                self.base_url, 
                json=payload, 
                headers={"Content-Type": "application/json"}
            )
            
            # Check if request was successful
            response.raise_for_status()
            
            # Parse JSON response
            valuation_data = response.json()
            
            # Extract and return key valuation information
            return {
                "estimated_value": valuation_data.get("estimated_value"),
                "confidence_level": valuation_data.get("confidence_level"),
                "value_range": {
                    "low": valuation_data.get("value_range", {}).get("low"),
                    "high": valuation_data.get("value_range", {}).get("high")
                }
            }
        
        except requests.RequestException as e:
            print(f"API Request Error: {e}")
            return None
        except json.JSONDecodeError:
            print("Error parsing API response")
            return None

def main():
    # Replace with your actual API key
    API_KEY = "your_api_key_here"
    
    # Create estimator instance
    estimator = HouseValueEstimator(API_KEY)
    
    # Example usage
    house_address = "123 Main St"
    house_zip = "94110"
    
    # Get house value estimation
    valuation = estimator.get_house_value(house_address, house_zip)
    
    if valuation:
        print("House Valuation Details:")
        print(f"Estimated Value: ${valuation['estimated_value']:,}")
        print(f"Confidence Level: {valuation['confidence_level']}%")
        print(f"Value Range: ${valuation['value_range']['low']:,} - ${valuation['value_range']['high']:,}")
    else:
        print("Could not retrieve house valuation")

if __name__ == "__main__":
    main()

import requests

class PatientService:

    BASE_URL = 'https://randomuser.me/api/'

    def get_fake_patient_data(self):
        response = requests.get(self.BASE_URL, params={'nat': 'br'})
        response.raise_for_status()

        user = response.json()['results'][0]

        return [{
            "name": f"{user['name']['first']} {user['name']['last']}",
            "email": user["email"],
            "phone": user["phone"]
        }]
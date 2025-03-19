from entertainment.models import Entertainment
from entertainment.serializers import EntertainmentSerializer

def handle_lock_entertainment(material_id):
    material = Entertainment.objects.get(id=material_id)
    serializer = EntertainmentSerializer(instance=material, data={'locked': True}, partial=True)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

        return True


def handle_unlock_entertainment(material_id):
    material = Entertainment.objects.get(id=material_id)
    serializer = EntertainmentSerializer(instance=material, data={'locked': False}, partial=True)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

        return True

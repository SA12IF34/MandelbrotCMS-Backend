from typing import Type, Dict, Any, Optional
from django.db.models import Model
from rest_framework.serializers import ModelSerializer, ValidationError

def get_all_objs(model: Type[Model], modelSerializer: Type[ModelSerializer], user: Any, order_by: str | list) -> Any:
    """
    Get all objects of model that user has created, ordered by certain field.
    Returns serialized objects data.

    - model: the model what to get objects from
    - modelSerializer: DRF serializer that is defined for the model
    - user: user which has created the object
    - order_by: field which to order by either ascendingly or descendingly (e.g. "id" or "-id")

    """
    order_params = order_by if isinstance(order_by, list) else [order_by]
    all_objs = model.objects.filter(user=user).order_by(*order_params)
    serializer = modelSerializer(instance=all_objs, many=True)

    return serializer.data


def get_objs_filter(model: Type[Model], modelSerializer: Type[ModelSerializer], user: Any, order_by: str, conditions: Dict[str, Any]) -> Any:
    """
    Get all objects of model that are created by user and match the condidions dictionary, and ordered by specified field.\n
    Returns object data from modelSerializer.data dictionary, 
    raises model.DoesNotExist error if no objects found.
    """

    objs = model.objects.filter(user=user, **conditions).order_by(order_by)
    serializer = modelSerializer(instance=objs, many=True)

    return serializer.data


def get_obj_by(model: Type[Model], modelSerializer: Type[ModelSerializer], user: Any, by: Dict[str, Any]) -> Optional[Any]:
    
    """
    Return desired object and it's data, the object is determined by the <by> parameter.\n
    Return model object and model object data dictionary, raises model.DoesNotExist if no object founded.
    """
    obj = model.objects.get(user=user, **by)    
    serializer = modelSerializer(instance=obj)
    
    return obj, serializer.data
    

def patch_update_obj(model: Type[Model], modelSerializer: Type[ModelSerializer], user: Any, by: Dict[str, Any], new_data: Dict[str, Any]) -> Any:
    
    """
    Update a part of object data with <new_data> parameter.\n
    Returns True on success, otherwise raises ValidationError.
    """
    
    obj = model.objects.get(user=user, **by)
    serializer = modelSerializer(instance=obj, data=new_data, partial=True)

    if serializer.is_valid():
        serializer.save()

        return True
            
    raise ValidationError

    
def delete_obj(model: Type[Model], user: Any, by: Dict[str, Any]) -> Optional[bool]:
    
    "Deletes an object from db."

    
    obj = model.objects.get(user=user, **by)
    obj.delete()

    return True
    
    

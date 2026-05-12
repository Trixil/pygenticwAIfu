some_car = {
    "carName": "mr meow meow",
    "engineName": "vroom engine"
}


class Car(BaseModel):
    id: str = ""
    carName: str = ""
    engineName: str = ""
    tag: list[str] = Field(default_factory=list)


Car.model_validate(some_car)


class pencil(BaseModel):
    id: str  = ""
    leadlength: float = 0.0


class utensilCollection(BaseModel):
    title: str = ""
    utensil: list[pencil] = Field(default_factory=list)


raw_utensil = {"title": "utensil1", "utensil": [
               {"id": "pencil1", "leadlength": 5.0}, {"id": "pencil2", "leadlength": 6.1}]}


clean_utensil = utensilCollection.model_validate(raw_utensil)
clean_utensil.utensil[1].id
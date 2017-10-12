
def ValidatePostItems(expectedFields, optionalFields, request, saveObj, atleastOne={}):
    for item in expectedFields:
        print (item, request.POST)
        if item not in request.POST:
            raise ValueError("Value not passed in post! " + item)
        setattr(saveObj, expectedFields[item], request.POST[item])
# optional inputs, dropdowns, and text areas
    for item in optionalFields:
        if item in request.POST:
            # validate emails
            setattr(saveObj, optionalFields[item], request.POST[item])
# Checkboxes, optional and expected
    if len( atleastOne ) > 0:
        found = []

        for key in atleastOne:
            for item in atleastOne[key]:
                if item in request.POST:
                    found.append(item)
            if len ( found ) == 0: raise ValueError("Value not passed in post!")
            print (found)
            setattr(saveObj, key, found)

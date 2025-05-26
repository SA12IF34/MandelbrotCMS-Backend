import json



with open('old-notes.json', 'r', encoding='utf-8') as notes:
    notes_data = json.load(notes)
    final_data = []
    i=0
    while i < len(notes_data):
    
        if 'content' in notes_data[i]['fields']:
            final_data.append(notes_data[i])

        

        i+=1


with open('notes.json', 'w', encoding='utf-8') as file:
    json.dump(final_data, file, indent=2)
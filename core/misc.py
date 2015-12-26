from random import randint


def make_readonly(form):
    for f in form.fields:
        form.fields[f].widget.attrs['disabled'] = True

    return form


def choose_and_remove(list):
    if not list:
        raise AttributeError("Empty list passed to choose_and_remove")

    index = randint(0, len(list) - 1)
    item = list[index]
    del list[index]

    return item

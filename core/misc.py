def make_readonly(form):
    for f in form.fields:
        form.fields[f].widget.attrs['readonly'] = True

    return form

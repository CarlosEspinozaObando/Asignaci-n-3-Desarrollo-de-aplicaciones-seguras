def login(request: Request):
    """
    Muestra el formulario de login.
    """
    return templates.TemplateResponse("login.html", {"request": request})
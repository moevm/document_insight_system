def includeme(config):
    # config.add_static_view(name = 'ViewerJS', path = 'templater:static/ViewerJS')
    config.add_static_view('static/css', 'static/css')
    config.add_static_view('static/js', 'static/js')
    config.add_static_view('static/img', 'static/img')
    config.add_static_view('ViewerJS', 'static/ViewerJS')
    config.add_route('home', '/')
    config.add_route('upload', '/upload')
    config.add_route('files', '/files')
    config.add_route('verify', '/verify')
    config.add_route('render', '/render')
    config.add_route('locale', '/locale')
    
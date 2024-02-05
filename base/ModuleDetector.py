class ModuleDetector:
    apps_to_detect = []
    data = {}

    def add_module_app(self, app):
        self.apps_to_detect.append(app)

    def get_module_data(self):
        return self.data

    def detect(self):
        for app in self.apps_to_detect:
            self.data[app.get_name()] = app.process()

        self.apps_to_detect.clear()

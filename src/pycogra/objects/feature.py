#!/usr/bin/env/python3

from src.pycogra.objects.cogra_types import HeaderFeatureType, HeaderRole, HeaderClassifier, \
    OPERATING_SYSTEM_PLATFORM, WINDOWS_TYPE, UNIX_LINUX_TYPE


class Type(object):
    def __init__(self, role):
        assert isinstance(role, HeaderRole)
        self.type = role
        self.classifier = None

    def set_classifier(self, classifier):
        assert isinstance(classifier, HeaderClassifier)
        self.classifier = classifier


class OperatingSystem(object):
    def __init__(self, platform):
        assert isinstance(platform, OPERATING_SYSTEM_PLATFORM)
        self.platform = platform
        self.value = None

    def set_value(self, value):
        if self.platform == OPERATING_SYSTEM_PLATFORM.WINDOWS:
            assert isinstance(value, WINDOWS_TYPE)
        elif self.platform == OPERATING_SYSTEM_PLATFORM.UNIX_LINUX:
            assert isinstance(value, UNIX_LINUX_TYPE)
        self.value = value

    def set_classifier(self, classifier):
        assert isinstance(classifier, HeaderClassifier)
        self.classifier = classifier


class Feature(object):
    def __init__(self, feature_type):
        self.ft = feature_type
        self.value = None

    def set_value(self, value):
        if self.ft == HeaderFeatureType.FT_NAME:
            assert isinstance(value, str)
        if self.ft == HeaderFeatureType.FT_OTHER:
            assert isinstance(value, str)
        elif self.ft == HeaderFeatureType.FT_ROLE:
            assert isinstance(value, Type)
        elif self.ft == HeaderFeatureType.FT_OPERATING_SYSTEM:
            assert isinstance(value, OperatingSystem)
        self.value = value


if __name__ == "__main__":
    f = Feature(HeaderFeatureType.FT_NAME)
    f.set_value("hello")
    # f.setValue(1)
    f.ft = HeaderFeatureType.FT_ROLE
    r = Type(HeaderRole.TYPE_SERVER)
    r.set_classifier(HeaderClassifier.CLASS_DPI)
    f.set_value(r)

    f2 = Feature(HeaderFeatureType.FT_OPERATING_SYSTEM)
    os = OperatingSystem(OPERATING_SYSTEM_PLATFORM.WINDOWS)
    type = WINDOWS_TYPE(1,3)
    os.set_value(type)
    f2.set_value(os)
import abc


class AttributeProvider(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get(self):
        pass

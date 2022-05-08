from config import config


def help(**kwargs):
    def wrapper(*args):
        kwargs.update({"command": config["prefix"] + kwargs["command"]})
        if kwargs["permissions"] == "dev":
            kwargs.update({"command": kwargs["command"] + "*"})
        else:
            pass
        
        return kwargs

    return wrapper


class Aliases:
    @classmethod
    def commands(cls):
        return [
            cls.new_aliase_dev, cls.new_aliase,
            cls.delete_aliase_dev, cls.delete_aliase,
            cls.aliases
        ]


    @help(
        command = f"Новый алиас",
        args = {"алиас": str},
        permissions = "dev"
    )
    def new_aliase_dev(self):
        pass


    @help(
        command = f"Новый алиас",
        args = {"алиас": str},
        permissions = "all"
    )
    def new_aliase(self):
        pass


    @help(
        command = f"Удалить алиас",
        args = {"индекс": int},
        permissions = "dev"
    )
    def delete_aliase_dev(self):
        pass


    @help(
        command = f"Удалить алиас",
        args = {"индекс": int},
        permissions = "all"
    )
    def delete_aliase(self):
        pass


    @help(
        command = f"Алиасы",
        args = {"алиас": str},
        permissions = "all"
    )
    def aliases(self):
        pass


for i in Aliases.commands():
    print(i)
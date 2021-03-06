# Pick a software and lets do this!

from i18n.en import En as i18n # ENGLISH
import main
import timer

timer.Timer.verbose = True

def Start():
    """
    Lets do this!
    """
    try: # Test for Maya
        import view.maya as view
        import model.maya as model
        main.Main(i18n, view, model, "maya")
    except ImportError:
        raise RuntimeError, "Sorry, your software is not supported."



if __name__ == '__main__':
    Start()

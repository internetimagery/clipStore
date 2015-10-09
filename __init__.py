# Pick a software and lets do this!

import i18n.en as i18n # ENGLISH
import main

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

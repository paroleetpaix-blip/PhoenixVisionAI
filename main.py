from launcher.splash import SplashScreen

from core.engine import PhoenixEngine



# =====================================
# Phoenix Vision AI
# Application Entry Point
# =====================================


# 1 - Splash Screen

splash = SplashScreen()

splash.show()



# 2 - Démarrage du moteur

engine = PhoenixEngine()

engine.start()



# 3 - Analyse

engine.analyze("videos/route.mp4")



# 4 - Arrêt

engine.stop()
from lazytask.app import LazyTaskApp
from lazytask.infrastructure.mock_backend import MockBackend

def main():
    app = LazyTaskApp(backend=MockBackend())
    app.run()

if __name__ == "__main__":
    main()

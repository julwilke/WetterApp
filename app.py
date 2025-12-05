from backend import dashboard

def main():
    app = dashboard.WeatherDashboard()
    app.run()

if __name__ == "__main__":
    main()

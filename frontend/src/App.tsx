import LandingPage from "./pages/LandingPage";
import AuthPage from "./pages/AuthPage";
import OnboardingPage from "./pages/OnboardingPage";
import DashboardPage from "./pages/DashboardPage";

export default function App() {
  const path = window.location.pathname;

  if (path === "/auth") {
    return <AuthPage />;
  }

  if (path === "/onboarding") {
    return <OnboardingPage />;
  }

  if (path === "/dashboard") {
    return <DashboardPage />;
  }

  return <LandingPage />;
}
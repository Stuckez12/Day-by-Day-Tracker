import PageWrapper from "components/common/PageWrapper";
import WelcomeText from "components/common/WelcomeText";
import RatingBar from "components/rating/RatingBar";

function LandingPage() {
  return (
    <PageWrapper>
      <h1>Landing Page</h1>
      <WelcomeText />
      <RatingBar />
    </PageWrapper>
  );
}

export default LandingPage;

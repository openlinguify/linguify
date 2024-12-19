import React from "react";
import { ProgressBar, Card } from "react-bootstrap";

type Props = {
    progress: number;
    badges: string[];
};

const LearningProgress: React.FC<Props> = ({ progress, badges }) => {
    return (
        <section className="mb-8">
        <Card className="mb-4 shadow">
            <Card.Body>
                <h5>Learning Progress</h5>
    <ProgressBar now={progress} label={`${progress}%`} />
    </Card.Body>
    </Card>
    <div>
    <h5>Badges</h5>
    <div className="d-flex flex-wrap">
        {badges.length > 0 ? (
                badges.map((badge, index) => (
                    <span key={index} className="badge bg-success text-white me-2 mb-2 p-3 rounded">
                {badge}
                </span>
))
) : (
        <p>No badges earned yet.</p>
)}
    </div>
    </div>
    </section>
);
};

export default LearningProgress;

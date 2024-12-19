// frontend/src/components/features/course/CourseList.tsx
import React from "react";

// Types
type Course = {
    id: number;
    title: string;
    description?: string;
};

type Props = {
    courses: Course[];
};

const CourseList: React.FC<Props> = ({ courses }) => {
    if (courses.length === 0) {
        return <p className="text-gray-600">No courses found.</p>;
    }

    return (
        <section>
            <h2 className="text-xl font-semibold mb-4">My Courses</h2>
            <ul className="list-disc pl-5">
                {courses.map((course) => (
                    <li key={course.id} className="mb-2">
                        {course.title}
                    </li>
                ))}
            </ul>
        </section>
    );
};

export default CourseList;

const Course = () => {
    return (
      <div className="min-h-screen bg-background text-foreground flex flex-col items-center py-12 px-4">
        <div className="w-full max-w-5xl bg-card shadow-lg rounded-lg p-8">
          <h1 className="text-4xl font-bold text-primary mb-6 text-center">
            Course
          </h1>
          <p className="text-muted-foreground text-lg text-center mb-10">
            Welcome to the course page! Explore the lessons and resources below to start learning.
          </p>
  
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Lesson Card 1 */}
            <div className="bg-gradient-to-br from-[#792FCE] to-[#fdd47c] shadow-md rounded-md p-6 text-white hover:scale-105 transition-transform duration-300">
              <h2 className="text-xl font-semibold">Lesson 1</h2>
              <p>
                An introduction to the basics of this course.
              </p>
            </div>
  
            {/* Lesson Card 2 */}
            <div className="bg-gradient-to-br from-[#792FCE] to-[#fdd47c] shadow-md rounded-md p-6 text-white hover:scale-105 transition-transform duration-300">
              <h2 className="text-xl font-semibold">Lesson 2</h2>
              <p>
                Dive deeper into advanced concepts.
              </p>
            </div>
  
            {/* Lesson Card 3 */}
            <div className="bg-gradient-to-br from-[#792FCE] to-[#fdd47c] shadow-md rounded-md p-6 text-white hover:scale-105 transition-transform duration-300">
              <h2 className="text-xl font-semibold">Lesson 3</h2>
              <p>
                Practice and test your knowledge with challenges.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  };
  
  export default Course;
  
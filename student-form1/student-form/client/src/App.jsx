import StudentForm from "./StudentForm.jsx";

export default function App() {
  return (
    <main>
      <h1>Student information form</h1>
      <p className="sub">Fields marked with * are required.</p>
      <StudentForm />
    </main>
  );
}

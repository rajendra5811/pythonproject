class ExamMark(Base):
    __tablename__ = "exam_marks"

    mark_id: Mapped[int] = mapped_column(
        primary_key=True
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.student_id")
    )

    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.subject_id")
    )

    academic_year: Mapped[str] = mapped_column(
        String(9)
    )

    exam_type: Mapped[str] = mapped_column(
        String(30)
    )

    marks_obtained: Mapped[int] = mapped_column(
        Integer
    )

    max_marks: Mapped[int] = mapped_column(
        Integer
    )
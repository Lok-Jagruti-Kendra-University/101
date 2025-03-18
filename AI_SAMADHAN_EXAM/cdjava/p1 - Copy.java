import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import java.io.*;
import java.util.*;
import java.text.*;

class Course {
    private String courseName;
    private int courseId;
    private int studentCount;  // number of students enrolled
    private String examTime;  // Time slot for the exam

    public Course(String courseName, int courseId, int studentCount, String examTime) {
        this.courseName = courseName;
        this.courseId = courseId;
        this.studentCount = studentCount;
        this.examTime = examTime;
    }

    public String getCourseName() {
        return courseName;
    }

    public int getCourseId() {
        return courseId;
    }

    public int getStudentCount() {
        return studentCount;
    }

    public String getExamTime() {
        return examTime;
    }

    @Override
    public String toString() {
        return "Course: " + courseName + " (ID: " + courseId + "), Students: " + studentCount + ", Exam Time: " + examTime;
    }
}

class Room {
    private String roomName;
    private int capacity;  // max number of students a room can hold
    private boolean available;  // if the room is available
    private String bookedTime;  // time when the room is booked

    public Room(String roomName, int capacity) {
        this.roomName = roomName;
        this.capacity = capacity;
        this.available = true; // initially, the room is available
        this.bookedTime = ""; // No time slot booked initially
    }

    public String getRoomName() {
        return roomName;
    }

    public int getCapacity() {
        return capacity;
    }

    public boolean isAvailable() {
        return available;
    }

    public void setAvailable(boolean available) {
        this.available = available;
    }

    public String getBookedTime() {
        return bookedTime;
    }

    public void setBookedTime(String bookedTime) {
        this.bookedTime = bookedTime;
    }

    @Override
    public String toString() {
        return roomName + " (Capacity: " + capacity + ")";
    }
}

class ExamScheduler {
    private List<Course> courses;
    private List<Room> rooms;
    private Map<Course, Room> examSchedule;

    public ExamScheduler(List<Course> courses, List<Room> rooms) {
        this.courses = courses;
        this.rooms = rooms;
        this.examSchedule = new HashMap<>();
    }

    // Function to generate the exam schedule
    public void generateSchedule() {
        // Sort courses by student count in descending order to prioritize larger courses
        courses.sort((c1, c2) -> Integer.compare(c2.getStudentCount(), c1.getStudentCount()));

        for (Course course : courses) {
            Room assignedRoom = assignRoomToCourse(course);
            if (assignedRoom != null) {
                examSchedule.put(course, assignedRoom);
                assignedRoom.setAvailable(false);  // Room is now booked
                assignedRoom.setBookedTime(course.getExamTime());
                System.out.println(course + " assigned to " + assignedRoom);
            } else {
                System.out.println("No available room for " + course);
            }
        }
    }

    // Function to assign a room based on capacity and time availability
    private Room assignRoomToCourse(Course course) {
        for (Room room : rooms) {
            if (room.isAvailable() && room.getCapacity() >= course.getStudentCount() && !isTimeConflict(room, course)) {
                return room;
            }
        }
        return null;  // No room available for this course
    }

    // Check for time conflict in room bookings
    private boolean isTimeConflict(Room room, Course course) {
        return room.getBookedTime().equals(course.getExamTime());
    }

    // Display the generated schedule
    public void displaySchedule() {
        System.out.println("\n--- Exam Schedule ---");
        for (Map.Entry<Course, Room> entry : examSchedule.entrySet()) {
            System.out.println(entry.getKey() + " -> " + entry.getValue());
        }
    }

    // Export the exam schedule to an Excel file
    public void exportScheduleToExcel(String fileName) {
        Workbook workbook = new XSSFWorkbook();
        Sheet sheet = workbook.createSheet("Exam Schedule");

        // Create header row
        Row headerRow = sheet.createRow(0);
        headerRow.createCell(0).setCellValue("Course Name");
        headerRow.createCell(1).setCellValue("Course ID");
        headerRow.createCell(2).setCellValue("Student Count");
        headerRow.createCell(3).setCellValue("Exam Time");
        headerRow.createCell(4).setCellValue("Room Assigned");

        int rowNum = 1;

        // Create data rows
        for (Map.Entry<Course, Room> entry : examSchedule.entrySet()) {
            Row row = sheet.createRow(rowNum++);
            row.createCell(0).setCellValue(entry.getKey().getCourseName());
            row.createCell(1).setCellValue(entry.getKey().getCourseId());
            row.createCell(2).setCellValue(entry.getKey().getStudentCount());
            row.createCell(3).setCellValue(entry.getKey().getExamTime());
            row.createCell(4).setCellValue(entry.getValue().getRoomName());
        }

        // Auto-size columns for better readability
        for (int i = 0; i < 5; i++) {
            sheet.autoSizeColumn(i);
        }

        // Write the workbook to a file
        try (FileOutputStream fileOut = new FileOutputStream(fileName)) {
            workbook.write(fileOut);
            workbook.close();
            System.out.println("Exam schedule exported to " + fileName);
            System.out.println(Hello World);
        } catch (IOException e) {
            System.out.println("Error exporting to Excel: " + e.getMessage());
        }
    }
}

class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        List<Course> courses = new ArrayList<>();
        List<Room> rooms = new ArrayList<>();

        // User input for courses
        System.out.println("Enter number of courses:");
        int numCourses = Integer.parseInt(scanner.nextLine());

        for (int i = 0; i < numCourses; i++) {
            System.out.println("Enter details for course " + (i + 1) + ":");

            System.out.print("Course Name: ");
            String courseName = scanner.nextLine();

            System.out.print("Course ID: ");
            int courseId = Integer.parseInt(scanner.nextLine());

            System.out.print("Number of Students: ");
            int studentCount = Integer.parseInt(scanner.nextLine());

            System.out.print("Exam Time (HH:mm): ");
            String examTime = scanner.nextLine();

            courses.add(new Course(courseName, courseId, studentCount, examTime));
        }

        // User input for rooms
        System.out.println("\nEnter number of rooms:");
        int numRooms = Integer.parseInt(scanner.nextLine());

        for (int i = 0; i < numRooms; i++) {
            System.out.println("Enter details for room " + (i + 1) + ":");

            System.out.print("Room Name: ");
            String roomName = scanner.nextLine();

            System.out.print("Room Capacity: ");
            int capacity = Integer.parseInt(scanner.nextLine());

            rooms.add(new Room(roomName, capacity));
        }

        // Create the exam scheduler and generate the schedule
        ExamScheduler scheduler = new ExamScheduler(courses, rooms);
        scheduler.generateSchedule();

        // Display the generated schedule
        scheduler.displaySchedule();

        // Export the schedule to Excel
        scheduler.exportScheduleToExcel("exam_schedule.xlsx");
    }
}



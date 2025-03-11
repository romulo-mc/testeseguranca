public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");

        // Declaração de uma variável não utilizada - SonarQube deve detectar isso como um code smell.
        int unusedVariable = 5;
    }
}

import java.io.IOException;
public class TestFetch {
    public static void main(String[] args) throws IOException {
        HttpClient client = new HttpClient("www.baidu.com", 80);
        HttpResponse resp = client.doGET("/");
        System.out.println("Status: " + resp.getStatusCode());
        System.out.println("Body length: " + (resp.getBody() != null ? resp.getBody().length() : "null"));
        System.out.println("Body:\n" + resp.getBody());
    }
}


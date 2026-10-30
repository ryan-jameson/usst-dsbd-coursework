import java.util.HashMap;
import java.util.Map;

/**
 * HTTP 响应模型，封装状态行、状态码、响应头与响应体。
 */
public class HttpResponse {
    private String statusLine;
    private int statusCode;
    private final Map<String, String> headers = new HashMap<>();
    private String body;

    public String getStatusLine() {
        return statusLine;
    }

    public void setStatusLine(String statusLine) {
        this.statusLine = statusLine;
    }

    public int getStatusCode() {
        return statusCode;
    }

    public void setStatusCode(int statusCode) {
        this.statusCode = statusCode;
    }

    public Map<String, String> getHeaders() {
        return headers;
    }

    public void addHeader(String key, String value) {
        headers.put(key, value);
    }

    public String getHeader(String key) {
        return headers.get(key);
    }

    public String getBody() {
        return body;
    }

    public void setBody(String body) {
        this.body = body;
    }
}

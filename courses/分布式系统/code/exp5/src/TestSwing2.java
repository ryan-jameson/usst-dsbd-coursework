import javax.swing.*;
public class TestSwing2 {
    public static void main(String[] args) throws Exception {
        HttpClient client = new HttpClient("www.baidu.com", 80);
        String html = client.doGET("/").getBody();
        String safeHtml = html.replaceAll("(?is)<script.*?>.*?</script>", "")
                                          .replaceAll("(?is)<style.*?>.*?</style>", "");
        JEditorPane p = new JEditorPane();
        p.setContentType("text/html");
        p.setText(safeHtml);
        System.out.println("Parsed text: " + p.getText().length() + " chars");
        System.out.println("Parsed preview: " + p.getText().substring(0, Math.min(200, p.getText().length())));
    }
}


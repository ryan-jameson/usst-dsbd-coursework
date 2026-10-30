import javax.swing.*;
public class TestSwing3 {
    public static void main(String[] args) throws Exception {
        HttpClient client = new HttpClient("www.baidu.com", 80);
        String html = client.doGET("/").getBody();
        String bodyContent = html;
        if (html.contains("<body") && html.contains("</body>")) {
             bodyContent = html.substring(html.indexOf("<body"), html.indexOf("</body>") + 7);
        }
        String safeHtml = bodyContent.replaceAll("(?is)<script.*?>.*?</script>", "")
                                     .replaceAll("(?is)<style.*?>.*?</style>", "")
                                     .replaceAll("(?is)<link.*?>", "");
        JEditorPane p = new JEditorPane();
        p.setContentType("text/html");
        p.setText(safeHtml);
        System.out.println("Parsed preview: " + p.getText());
    }
}


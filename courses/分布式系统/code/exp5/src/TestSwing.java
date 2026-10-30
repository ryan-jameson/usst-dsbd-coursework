import javax.swing.*;
public class TestSwing {
    public static void main(String[] args) throws Exception {
        HttpClient client = new HttpClient("www.baidu.com", 80);
        String html = client.doGET("/").getBody();
        String safeHtml = html.replaceAll("(?is)<script.*?>.*?</script>", "")
                                          .replaceAll("(?is)<style.*?>.*?</style>", "");
        JFrame f = new JFrame("Test");
        JEditorPane p = new JEditorPane();
        p.setContentType("text/html");
        p.setText(safeHtml);
        f.add(new JScrollPane(p));
        f.setSize(800, 600);
        f.setVisible(true);
        f.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
    }
}


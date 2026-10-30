import javafx.application.Application;
import javafx.application.Platform;
import javafx.beans.value.ObservableValue;
import javafx.concurrent.Worker;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.scene.web.WebEngine;
import javafx.scene.web.WebView;
import javafx.stage.Stage;

public class ModernBrowser extends Application {

    private WebEngine engine;
    private TextField urlField;
    private ProgressBar progressBar;
    private Label statusLabel;
    
    private BorderPane root;
    private BorderPane topBar;
    private HBox searchBox;
    private VBox homeView;
    private VBox postView; // 新增 POST 视图
    private TabPane tabPane;
    private TextArea sourceArea;
    private TextArea headerArea;
    private TextField homeUrlField;

    @Override
    public void start(Stage stage) {
        root = new BorderPane();
        root.getStyleClass().add("root");

        // 1. 顶部控制栏 (右上角小房子, 居中搜索框)
        topBar = new BorderPane();
        topBar.getStyleClass().add("top-bar");
        
        Button homeBtn = new Button("🏠 首页");
        homeBtn.getStyleClass().add("home-btn");
        homeBtn.setOnAction(e -> showHome());
        
        Button postModeBtn = new Button("📝 POST 测试");
        postModeBtn.setStyle("-fx-background-color: #fbbc05; -fx-text-fill: black; -fx-font-weight: bold;");
        postModeBtn.setOnAction(e -> showPostView());
        
        HBox topButtons = new HBox(10, homeBtn, postModeBtn);
        topButtons.setAlignment(Pos.CENTER_RIGHT);
        topBar.setRight(topButtons);
        
        searchBox = new HBox(10);
        searchBox.setAlignment(Pos.CENTER);
        
        urlField = new TextField();
        urlField.setPromptText("🔍 搜索或输入网址...");
        urlField.getStyleClass().add("omnibox");
        urlField.setOnAction(e -> loadUrl(urlField.getText()));
        
        Button goBtn = new Button("前往");
        goBtn.getStyleClass().add("go-btn");
        goBtn.setOnAction(e -> loadUrl(urlField.getText()));
        
        searchBox.getChildren().addAll(urlField, goBtn);

        // 2. 首页视图 (Home View)
        homeView = new VBox(45);
        homeView.setAlignment(Pos.CENTER);
        
        // 使用一个占位 Label 来模拟增加字间距（JavaFX原生不支持CSS letter-spacing 很好，但可以通过空格模拟或仅利用字体大小）
        Label title = new Label("Internet 应用");
        title.getStyleClass().add("home-title");

        HBox homeSearchBox = new HBox(15);
        homeSearchBox.setAlignment(Pos.CENTER);
        
        homeUrlField = new TextField();
        homeUrlField.setPromptText("🔍 搜索或输入网址前往...");
        homeUrlField.getStyleClass().add("home-search");
        homeUrlField.setOnAction(e -> loadUrl(homeUrlField.getText()));
        
        Button homePostBtn = new Button("前往");
        homePostBtn.getStyleClass().add("home-btn-post");
        homePostBtn.setOnAction(e -> loadUrl(homeUrlField.getText()));
        
        homeSearchBox.getChildren().addAll(homeUrlField, homePostBtn);
        homeView.getChildren().addAll(title, homeSearchBox);

        // 新增：2.5 POST 测试视图
        postView = new VBox(25);
        postView.setAlignment(Pos.CENTER);
        postView.setStyle("-fx-padding: 40px; -fx-background-color: #202124;");
        
        Label postTitle = new Label("HTTP POST 调试器");
        postTitle.setStyle("-fx-font-size: 28px; -fx-text-fill: #e8eaed; -fx-font-weight: bold; -fx-font-family: 'Segoe UI', sans-serif;");
        
        // URL 输入组
        VBox urlGroup = new VBox(8);
        urlGroup.setAlignment(Pos.CENTER_LEFT);
        urlGroup.setMaxWidth(600);
        Label lblUrl = new Label("目标地址 (Target URL):");
        lblUrl.setStyle("-fx-text-fill: #9aa0a6; -fx-font-size: 13px; -fx-font-weight: bold;");
        
        TextField postUrlField = new TextField();
        postUrlField.setPromptText("例如 http://httpbin.org/post");
        postUrlField.setStyle("-fx-pref-width: 600px; -fx-font-size: 15px; -fx-padding: 12px; -fx-background-color: #303134; -fx-text-fill: #e8eaed; -fx-background-radius: 8; -fx-border-color: #5f6368; -fx-border-radius: 8; -fx-border-width: 1px;");
        urlGroup.getChildren().addAll(lblUrl, postUrlField);

        // Body 输入组
        VBox bodyGroup = new VBox(8);
        bodyGroup.setAlignment(Pos.CENTER_LEFT);
        bodyGroup.setMaxWidth(600);
        Label lblBody = new Label("请求体数据 (Body Data - application/x-www-form-urlencoded):");
        lblBody.setStyle("-fx-text-fill: #9aa0a6; -fx-font-size: 13px; -fx-font-weight: bold;");
        
        TextArea postDataArea = new TextArea();
        postDataArea.setPromptText("键值对格式: key1=value1&key2=value2\n例如: name=张三&score=100");
        // 注意：TextArea 的背景色通常需要控制 -fx-control-inner-background
        postDataArea.setStyle("-fx-pref-height: 200px; -fx-font-family: 'Consolas', monospace; -fx-font-size: 14px; -fx-control-inner-background: #303134; -fx-text-fill: #81c995; -fx-background-color: #303134; -fx-border-color: #5f6368; -fx-border-radius: 8; -fx-background-radius: 8;");
        bodyGroup.getChildren().addAll(lblBody, postDataArea);
        
        Button sendPostBtn = new Button("发送 POST 请求 🚀");
        String btnNormalStyle = "-fx-background-color: #8ab4f8; -fx-text-fill: #202124; -fx-font-size: 16px; -fx-font-weight: bold; -fx-padding: 12 30; -fx-cursor: hand; -fx-background-radius: 20;";
        String btnHoverStyle = "-fx-background-color: #aecbfa; -fx-text-fill: #202124; -fx-font-size: 16px; -fx-font-weight: bold; -fx-padding: 12 30; -fx-cursor: hand; -fx-background-radius: 20;";
        sendPostBtn.setStyle(btnNormalStyle);
        sendPostBtn.setOnMouseEntered(e -> sendPostBtn.setStyle(btnHoverStyle));
        sendPostBtn.setOnMouseExited(e -> sendPostBtn.setStyle(btnNormalStyle));
        
        sendPostBtn.setOnAction(e -> sendPostRequest(postUrlField.getText(), postDataArea.getText()));
        
        postView.getChildren().addAll(postTitle, urlGroup, bodyGroup, sendPostBtn);

        // 3. 浏览器和源码视图 (TabPane)
        tabPane = new TabPane();
        tabPane.getStyleClass().add("tab-pane");
        tabPane.setTabClosingPolicy(TabPane.TabClosingPolicy.UNAVAILABLE);
        
        // 包裹 WebView 以增加 Padding
        StackPane webViewContainer = new StackPane();
        webViewContainer.setStyle("-fx-padding: 10px; -fx-background-color: #202124;");
        WebView webView = new WebView();
        // 给 webView 加个简单的阴影或圆角（可选）
        webView.setStyle("-fx-effect: dropshadow(three-pass-box, rgba(0,0,0,0.4), 8, 0, 0, 0);");
        engine = webView.getEngine();
        webViewContainer.getChildren().add(webView);
        
        Tab webTab = new Tab("网页");
        webTab.setContent(webViewContainer);
        
        StackPane sourceContainer = new StackPane();
        sourceContainer.setStyle("-fx-padding: 10px; -fx-background-color: #202124;");
        sourceArea = new TextArea();
        sourceArea.setEditable(false);
        sourceArea.setWrapText(true);
        sourceArea.getStyleClass().add("text-area");
        sourceContainer.getChildren().add(sourceArea);

        Tab sourceTab = new Tab("源代码");
        sourceTab.setContent(sourceContainer);
        
        StackPane headerContainer = new StackPane();
        headerContainer.setStyle("-fx-padding: 10px; -fx-background-color: #202124;");
        headerArea = new TextArea();
        headerArea.setEditable(false);
        headerArea.setWrapText(true);
        headerArea.getStyleClass().add("text-area");
        headerContainer.getChildren().add(headerArea);
        
        Tab headerTab = new Tab("请求头");
        headerTab.setContent(headerContainer);
        
        tabPane.getTabs().addAll(webTab, sourceTab, headerTab);

        // 4. 底部状态栏
        HBox bottomBar = new HBox(10);
        bottomBar.setAlignment(Pos.CENTER_LEFT);
        bottomBar.getStyleClass().add("bottom-bar");
        
        progressBar = new ProgressBar(0);
        progressBar.setPrefWidth(150);
        progressBar.setVisible(false);
        progressBar.setStyle("-fx-accent: #4285F4;"); // Material blue
        
        statusLabel = new Label("就绪");
        statusLabel.setStyle("-fx-text-fill: #5f6368; -fx-font-size: 12px;");
        bottomBar.getChildren().addAll(progressBar, statusLabel);

        // 5. 事件监听与组装
        engine.locationProperty().addListener((obs, oldUrl, newUrl) -> {
            if (newUrl != null && !newUrl.isEmpty()) {
                urlField.setText(newUrl);
            }
        });

        engine.getLoadWorker().stateProperty().addListener((obs, oldState, newState) -> {
            if (newState == Worker.State.RUNNING || newState == Worker.State.SCHEDULED) {
                progressBar.setVisible(true);
                statusLabel.setText("正在加载: " + engine.getLocation());
            } else if (newState == Worker.State.SUCCEEDED) {
                progressBar.setVisible(false);
                statusLabel.setText("加载完成");
                stage.setTitle(engine.getTitle() + " - JavaFX 浏览器");
                
                try {
                    String html = (String) engine.executeScript("document.documentElement.outerHTML");
                    sourceArea.setText("<html>\n" + html + "\n</html>");
                } catch(Exception ex) {
                    sourceArea.setText("无法获取源代码。");
                }
            } else if (newState == Worker.State.FAILED) {
                progressBar.setVisible(false);
                statusLabel.setText("加载失败");
            }
        });
        
        engine.getLoadWorker().progressProperty().addListener((obs, oldProg, newProg) -> {
            progressBar.setProgress(newProg.doubleValue());
        });

        engine.setOnAlert(event -> {
            Alert alert = new Alert(Alert.AlertType.INFORMATION);
            alert.setHeaderText(null);
            alert.setContentText(event.getData());
            alert.showAndWait();
        });

        root.setTop(topBar);
        root.setBottom(bottomBar);
        showHome(); // 初始显示首页
        
        Scene scene = new Scene(root, 1100, 750);
        try {
            scene.getStylesheets().add(getClass().getResource("style.css").toExternalForm());
        } catch (Exception e) {
            System.err.println("无法加载 style.css");
        }
        stage.setTitle("现代 Java 浏览器 - (完全内核解析)");
        stage.setScene(scene);
        stage.show();
    }

    private void showHome() {
        root.setCenter(homeView);
        topBar.setCenter(null); // 隐藏顶部搜索栏，只保留右侧按钮
        homeUrlField.setText("");
    }

    private void showPostView() {
        root.setCenter(postView);
        topBar.setCenter(null);
    }

    private void sendPostRequest(String urlStr, String postData) {
        if (urlStr == null || urlStr.trim().isEmpty()) {
            Alert alert = new Alert(Alert.AlertType.WARNING, "请输入 URL");
            alert.show();
            return;
        }
        
        String tempUrl = urlStr.trim();
        if (!tempUrl.startsWith("http://") && !tempUrl.startsWith("https://")) {
            tempUrl = "http://" + tempUrl;
        }
        final String finalTargetUrl = tempUrl;

        // 切换到结果视图
        root.setCenter(tabPane);
        
        // 🔒 POST 模式下锁定顶部栏，防止误触 GET 请求
        HBox postStatusBox = new HBox(15);
        postStatusBox.setAlignment(Pos.CENTER);
        
        Label methodLabel = new Label("POST 模式");
        methodLabel.setStyle("-fx-background-color: #fbbc05; -fx-text-fill: black; -fx-padding: 3 8; -fx-background-radius: 4; -fx-font-weight: bold;");
        
        Label urlLabel = new Label(finalTargetUrl);
        urlLabel.setStyle("-fx-text-fill: white; -fx-font-family: 'Consolas';");
        
        Button backToEditBtn = new Button("✏️ 修改参数 / 下一测");
        backToEditBtn.setStyle("-fx-cursor: hand; -fx-background-color: #444; -fx-text-fill: white;");
        backToEditBtn.setOnAction(e -> showPostView()); // 点击返回 POST 表单
        
        postStatusBox.getChildren().addAll(methodLabel, urlLabel, backToEditBtn);
        topBar.setCenter(postStatusBox); // 替换掉原来的 GET 搜索栏

        sourceArea.setText("正在发送 POST 请求...");
        headerArea.setText("正在等待响应...");
        
        // 使用 engine 加载一个加载中的提示
        engine.loadContent("<html><body style='background:#202124;color:white;'><h1>正在发送 POST 数据...</h1><p>目标: " + finalTargetUrl + "</p><p>数据: " + postData + "</p></body></html>");

        new Thread(() -> {
            try {
                // 1. 建立连接
                java.net.URL url = new java.net.URL(finalTargetUrl);
                java.net.HttpURLConnection conn = (java.net.HttpURLConnection) url.openConnection();
                conn.setRequestMethod("POST");
                conn.setDoOutput(true); // 允许输出 Body
                conn.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");
                conn.setRequestProperty("User-Agent", "Mozilla/5.0 (JavaFX POST Client)");
                
                // 2. 发送 POST 数据
                byte[] postBytes = postData.getBytes("UTF-8");
                conn.setRequestProperty("Content-Length", String.valueOf(postBytes.length));
                try (java.io.OutputStream os = conn.getOutputStream()) {
                    os.write(postBytes);
                }

                // 3. 读取响应
                StringBuilder sb = new StringBuilder();
                sb.append("=== 发送的 POST 请求 ===\n");
                sb.append("POST ").append(url.getPath()).append(" HTTP/1.1\n");
                sb.append("Content-Type: application/x-www-form-urlencoded\n");
                sb.append("Content-Length: ").append(postBytes.length).append("\n\n");
                sb.append(postData).append("\n\n");
                
                sb.append("=== 接收的 POST 响应 ===\n");
                int responseCode = conn.getResponseCode();
                sb.append(conn.getHeaderField(0)).append("\n"); // Status line
                
                for (java.util.Map.Entry<String, java.util.List<String>> entry : conn.getHeaderFields().entrySet()) {
                    if (entry.getKey() != null) {
                        sb.append(entry.getKey()).append(": ").append(String.join(", ", entry.getValue())).append("\n");
                    }
                }
                
                // 读取正文
                java.io.InputStream is = (responseCode >= 400) ? conn.getErrorStream() : conn.getInputStream();
                java.util.Scanner scanner = new java.util.Scanner(is, "UTF-8").useDelimiter("\\A");
                String responseBody = scanner.hasNext() ? scanner.next() : "";
                
                // 4. 更新 UI
                javafx.application.Platform.runLater(() -> {
                    // 更新 Header tab
                    headerArea.setText(sb.toString());
                    // 更新 源码 tab
                    sourceArea.setText(responseBody);
                    // 渲染 HTML 到浏览器视图
                    engine.loadContent(responseBody);
                });
                
            } catch (Exception ex) {
                javafx.application.Platform.runLater(() -> {
                    engine.loadContent("<html><body style='color:red'><h1>POST 请求失败</h1><p>" + ex.getMessage() + "</p></body></html>");
                    headerArea.setText("错误: " + ex.getMessage());
                });
            }
        }).start();
    }

    private void loadUrl(String url) {
        if (url == null || url.trim().isEmpty()) return;
        String tempUrl = url.trim();
        if (!tempUrl.startsWith("http://") && !tempUrl.startsWith("https://")) {
            tempUrl = "http://" + tempUrl; // HTTP 作为默认前缀
        }
        final String finalUrl = tempUrl; // 将 finalUrl 声明为 final 解决 lambda 引用问题
        
        // 切换到浏览器视图
        root.setCenter(tabPane);
        topBar.setCenter(searchBox); // 显示顶部搜索栏
        
        urlField.setText(finalUrl);
        sourceArea.setText("正在加载源代码...");
        headerArea.setText("正在抓取请求头信息...\n");
        engine.load(finalUrl);

        // 异步获取请求头信息
        new Thread(() -> {
            try {
                java.net.URL u = new java.net.URL(finalUrl);
                java.net.HttpURLConnection conn = (java.net.HttpURLConnection) u.openConnection();
                conn.setRequestMethod("GET");
                conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) JavaFX");
                conn.connect();
                
                StringBuilder sb = new StringBuilder();
                sb.append("=== 模拟发送的 HTTP GET 请求头 ===\n");
                sb.append("GET ").append(u.getPath().isEmpty() ? "/" : u.getPath()).append(" HTTP/1.1\n");
                sb.append("Host: ").append(u.getHost()).append("\n");
                sb.append("User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) JavaFX\n");
                sb.append("Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\n");
                sb.append("Connection: keep-alive\n\n");
                
                sb.append("=== 接收的 HTTP 响应头 ===\n");
                if (conn.getHeaderField(0) != null) {
                    sb.append(conn.getHeaderField(0)).append("\n"); // Status line
                }
                for (java.util.Map.Entry<String, java.util.List<String>> entry : conn.getHeaderFields().entrySet()) {
                    if (entry.getKey() != null) {
                        sb.append(entry.getKey()).append(": ").append(String.join(", ", entry.getValue())).append("\n");
                    }
                }
                
                javafx.application.Platform.runLater(() -> headerArea.setText(sb.toString()));
                conn.disconnect();
            } catch (Exception ex) {
                javafx.application.Platform.runLater(() -> headerArea.setText("获取请求头失败: " + ex.getMessage()));
            }
        }).start();
    }
    
    public static void main(String[] args) {
        launch(args);
    }
}
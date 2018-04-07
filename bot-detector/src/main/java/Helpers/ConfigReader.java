package Helpers;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class ConfigReader {
    public static Map<String, String> read(String configFile) {
        Map<String, String> config = new HashMap<>();
        Pattern configPattern = Pattern.compile("([^=]+)=([^ ]*).*(#[^\\n]*|.*)");
        try (BufferedReader br = new BufferedReader(new FileReader(configFile))) {
            String line;
            while((line = br.readLine()) != null) {
                Matcher m = configPattern.matcher(line);
                if (m.find()) {
                    config.put(m.group(1), m.group(2));
                }
            }
        } catch (IOException e) {
            System.err.println("Положите конфиг для подключения к виртуалке в " + configFile);
            System.err.println("Скопируйте " + configFile +".template и поменяйте настройки");
            return null;
        }
        return config;
    }
}

package Utils;

public class IPConverter {
    public static int ipToInt(String ip) {
        if (ip == null) {
            throw new NullPointerException("IP is null");
        }

        int r = 0;
        int d = 0;
        int dots = 0;
        int length = ip.length();

        for (int i = 0; i < length; i++) {
            char c = ip.charAt(i);
            if (c == '.') {
                dots++;
                if (dots > 3 || d > 255) {
                    throw new IllegalArgumentException(ip);
                }
                r = (r << 8) + d;
                d = 0;
            } else if (c >= '0' && c <= '9') {
                d = d * 10 + (c - '0');
            } else {
                throw new IllegalArgumentException(ip);
            }
        }

        if (dots != 3 || d > 255) {
            throw new IllegalArgumentException(ip);
        }
        return (r << 8) + d;
    }

    public static String intToIp(int ip) {
        return new StringBuilder(16)
                .append(ip >>> 24).append('.')
                .append((ip >>> 16) & 0xff).append('.')
                .append((ip >>> 8) & 0xff).append('.')
                .append(ip & 0xff).toString();
    }
}

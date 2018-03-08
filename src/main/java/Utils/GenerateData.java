package Utils;

import com.opencsv.CSVWriter;
import java.io.Writer;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.io.IOException;
import java.util.concurrent.ThreadLocalRandom;

public class GenerateData {

    public static final long MIN_IN_SECONDS = 1518998400L;    //Human time (GMT): Monday, February 19, 2018 12:00:00 AM
    public static final long MAX_IN_SECONDS = 1519603200L;    //Human time (GMT): Monday, February 26, 2018 12:00:00 AM

    public static final long FIRST_DAY_7PM_IN_SECONDS = 1519066800L;  //Human time (GMT): Monday, February 19, 2018 7:00:00 PM
    public static final long SECOND_DAY_7PM_IN_SECONDS = 1519153200L; //Human time (GMT): Tuesday, February 20, 2018 7:00:00 PM
    public static final long THIRD_DAY_7PM_IN_SECONDS = 1519239600L;  //Human time (GMT): Wednesday, February 21, 2018 7:00:00 PM
    public static final long FOURTH_DAY_7PM_IN_SECONDS = 1519326000L; //Human time (GMT): Thursday, February 22, 2018 7:00:00 PM
    public static final long FIFTH_DAY_7PM_IN_SECONDS = 1519412400L;  //Human time (GMT): Friday, February 23, 2018 7:00:00 PM
    public static final long SIXTH_DAY_7PM_IN_SECONDS = 1519498800L;  //Human time (GMT): Saturday, February 24, 2018 7:00:00 PM
    public static final long SEVENTH_DAY_7PM_IN_SECONDS = 1519585200L;//Human time (GMT): Sunday, February 25, 2018 7:00:00 PM

    public static void main(String[] args) throws IOException {

        long ts;

        try (Writer writer = Files.newBufferedWriter(Paths.get("./res/generated_data.csv"));

             CSVWriter csvWriter = new CSVWriter(writer,
                    CSVWriter.DEFAULT_SEPARATOR,
                    CSVWriter.NO_QUOTE_CHARACTER,
                    CSVWriter.DEFAULT_ESCAPE_CHARACTER,
                    CSVWriter.DEFAULT_LINE_END)
        ) {
            String[] headerRecord = {"IP", "TIMESTAMP", "BOT_OR_HUMAN"};
            csvWriter.writeNext(headerRecord);

            // Генерируем данные для ботов
            for(int k = 0; k < 10; k++) {
                int ip = Utils.IPConverter.ipToInt(genRandIP());    // так исторически сложилось
                for(int i = 0; i < 14_0; i++) {
                    ts = ThreadLocalRandom.current().nextLong(MIN_IN_SECONDS, MAX_IN_SECONDS + 1);
                    csvWriter.writeNext(new String[]{Integer.toString(ip), Long.toString(ts), "bot"});
                }
            }

            // Генерируем данные для хуманов
            for(int k = 0; k < 10; k++) {
                int ip = Utils.IPConverter.ipToInt(genRandIP());
                for(int j = 0; j < 20; j++) {
                    ts = ThreadLocalRandom.current().nextLong(FIRST_DAY_7PM_IN_SECONDS, FIRST_DAY_7PM_IN_SECONDS + 3600*2 + 1);
                    csvWriter.writeNext(new String[]{Integer.toString(ip), Long.toString(ts), "human"});

                    ts = ThreadLocalRandom.current().nextLong(SECOND_DAY_7PM_IN_SECONDS, SECOND_DAY_7PM_IN_SECONDS + 3600*2 + 1);
                    csvWriter.writeNext(new String[]{Integer.toString(ip), Long.toString(ts), "human"});

                    ts = ThreadLocalRandom.current().nextLong(THIRD_DAY_7PM_IN_SECONDS, THIRD_DAY_7PM_IN_SECONDS + 3600*2 + 1);
                    csvWriter.writeNext(new String[]{Integer.toString(ip), Long.toString(ts), "human"});

                    ts = ThreadLocalRandom.current().nextLong(FOURTH_DAY_7PM_IN_SECONDS, FOURTH_DAY_7PM_IN_SECONDS + 3600*2 + 1);
                    csvWriter.writeNext(new String[]{Integer.toString(ip), Long.toString(ts), "human"});

                    ts = ThreadLocalRandom.current().nextLong(FIFTH_DAY_7PM_IN_SECONDS, FIFTH_DAY_7PM_IN_SECONDS + 3600*2 + 1);
                    csvWriter.writeNext(new String[]{Integer.toString(ip), Long.toString(ts), "human"});

                    ts = ThreadLocalRandom.current().nextLong(SIXTH_DAY_7PM_IN_SECONDS, SIXTH_DAY_7PM_IN_SECONDS + 3600*2 + 1);
                    csvWriter.writeNext(new String[]{Integer.toString(ip), Long.toString(ts), "human"});

                    ts = ThreadLocalRandom.current().nextLong(SEVENTH_DAY_7PM_IN_SECONDS, SEVENTH_DAY_7PM_IN_SECONDS + 3600*2 + 1);
                    csvWriter.writeNext(new String[]{Integer.toString(ip), Long.toString(ts), "human"});
                }
            }
        }
    }

    public static String genRandIP() {
        String ip = ThreadLocalRandom.current().nextInt(256) + "." +
                ThreadLocalRandom.current().nextInt(256) + "." +
                ThreadLocalRandom.current().nextInt(256) + "." +
                ThreadLocalRandom.current().nextInt(256);
        return ip;
    }
}

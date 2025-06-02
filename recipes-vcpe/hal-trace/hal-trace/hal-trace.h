#ifndef HAL_TRACE_H_
#define HAL_TRACE_H_
#include <time.h>
#include <sys/time.h>
#include <execinfo.h>
#include <stdlib.h>  // for getenv()
#include <string.h>  // for strcasecmp()
#include <unistd.h>  // for getpid(), access()
#include <pthread.h> // for pthread_self()
#include <sys/syscall.h> // for SYS_gettid
#include <sys/types.h>   // for pid_t

#define LOG_FILE "/rdklogs/logs/" HAL_TRACE_FILE ".log"

#define TRACE_FUNCTION(...) do { \
    if (access("/nvram/.hal-trace", F_OK) == 0) { \
        void *bt_array[20]; \
        char **bt_strings; \
        int bt_size, i; \
        \
        /* Get system thread id */ \
        pid_t tid = syscall(SYS_gettid); \
        \
        /* Time handling with microsecond precision */ \
        struct timeval tv; \
        struct tm tm; \
        char timeBuff[40] = {0}; \
        \
        /* Get current timestamp with microseconds */ \
        gettimeofday(&tv, NULL); \
        localtime_r(&tv.tv_sec, &tm); \
        \
        /* Format timestamp with microseconds */ \
        sprintf(timeBuff, "%02d%02d%02d-%02d:%02d:%02d.%06ld", \
                tm.tm_year + 1900 - 2000, \
                tm.tm_mon + 1, \
                tm.tm_mday, \
                tm.tm_hour, \
                tm.tm_min, \
                tm.tm_sec, \
                tv.tv_usec); \
        \
        /* Log file handling */ \
        FILE *fp = fopen(LOG_FILE, "a"); \
        if (fp) { \
            fprintf(fp, "\n%s [%d:%d] @@@%s(%s)\n", timeBuff, getpid(), tid, __FUNCTION__, \
                    (sizeof(#__VA_ARGS__) > 1) ? #__VA_ARGS__ : ""); \
            \
            /* Only do backtrace if halbacktrace file exists */ \
            if (access("/nvram/.hal-backtrace", F_OK) == 0) { \
                bt_size = backtrace(bt_array, 20); \
                bt_strings = backtrace_symbols(bt_array, bt_size); \
                if (bt_strings) { \
                    for (i = 0; i < bt_size; i++) \
                        fprintf(fp, "    %s\n", bt_strings[i]); \
                    free(bt_strings); \
                } \
            } \
            fclose(fp); \
        } \
    } \
} while(0)

#endif /* HAL_TRACE_H_ */

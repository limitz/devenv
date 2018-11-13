#ifndef LOCK_H
#define LOCK_H

#include <QMutex>

#ifdef LOCK
#warn "LOCK() previously defined
#else

struct _LOCK {
    _LOCK(QMutex* mutex) { (_m=mutex)->lock(); }
    ~_LOCK() { _m->unlock(); }
    QMutex* _m;
};

#define LOCK(_) for (_LOCK _L(&(_)),*_OCK=&_L;_OCK;_OCK=nullptr)

inline void LOCK_example() {
    QMutex m1, m2;
    LOCK(m1) {
        qDebug("m1 locked");
        LOCK(m2) {
            qDebug("m2 locked");
        }
        qDebug("m2 unlocked");
    }
    qDebug("m1 unlocked");
}

#endif // LOCK
#endif // LOCK_H

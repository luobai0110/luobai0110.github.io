---
title: java多线程
date: 2024-12-20 11:02:54
category: 
  - java
tag:
  - java
---

### 调用run方法和调用start方法的区别

1. 调用start的方法会创建一个新的线程, 然后os会调用run方法
2. 调用run方法只是普通的调用方法, 并不会创建一个新的线程

### 线程的执行顺序

线程的执行顺序与调用start的位置无关, 只和os的调度有关

```java
public class TestMyThread {
    public static void main(String[] args) {
        for (int i = 0; i < 10; i++) {
            MyThread myThread = new MyThread(i);
            myThread.start();
        }
    }
}


class MyThread extends Thread{
    private final int i;

    public MyThread(int i) {
        this.i = i;
    }

    @Override
    public void run() {
        System.out.println(i);
    }
}
```

![image-20241220111452269](https://raw.githubusercontent.com/luobai0110/blogpic/main/image-20241220111452269.png)

### 使用带返回值的多线程

可以通过实现Callable接口实现带返回值的多线程, **注意java中启动线程最终都要回到Thread类的start方法**

```java
public class CallableDemo {
    public static void main(String[] args) {


        // 搭桥创建线程
        MyCallable myCallable = new MyCallable(1);

        FutureTask<Integer> futureTask = new FutureTask<>(myCallable);

        Thread t = new Thread(futureTask);
        t.start();

        try {
            System.out.println(futureTask.get());
        } catch (InterruptedException | ExecutionException e) {
            throw new RuntimeException(e);
        }
    }
}
class MyCallable implements Callable<Integer> {
    private final int i;
    public MyCallable(int i) {
        this.i = i;
    }
    @Override
    public Integer call() {
        return i;
    }
}
```

### 多线程的异常

线程之间共享堆区, 不共享栈区, 目的是多线程之间处理任务不相互影响, 单个线程发生异常时不影响其他线程.

```java
public static void main(String[] args) throws InterruptedException {
    Thread thread = new Thread(() -> {
        try {
            Thread.sleep(2000);
            System.out.println(1);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
    });
    thread.start();
    Thread thread1 = new Thread(() -> {
        try {
            Thread.sleep(5000);
            System.out.println(2);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
    });
    thread1.start();
    Thread.sleep(3000);
    System.out.println(3);


}
```

输出3所需时间, 至少三秒

### synchronized

此段执行代码如下: 

```java
public class TestAccount {
    public static void main(String[] args) throws InterruptedException {
        Account account = new Account();
        Thread t1 = new Thread(() -> {
            for (int i = 0; i < 5; i++) {
                account.deposit(1000);
            }
        });
        t1.setName("kunkun");
        Thread t2 = new Thread(() -> {
            for (int i = 0; i < 5; i++) {
                account.deposit(1000);
            }
        });
        t2.setName("qianqian");
        t1.start();
        t2.start();
        Thread.sleep(1500);
        System.out.println("账户余额为" + account.getBalance());
    }
}
```

作用: 保证原子操作;

加锁过程:

1. 所有线程参与抢锁
2. 抢到锁的线程, 同步执行代码
3. 执行代码后需要释放

#### synchronized 修饰方法

```java
public synchronized void deposit(double money) {
    balance = balance.add(BigDecimal.valueOf(money));
    System.out.println(Thread.currentThread().getName() + "balance:" + balance);
}
```

特点:

1. 隐式锁, 指的是在编程语言或框架中，不需要显式地使用锁（如互斥锁、读写锁等）来控制对共享资源的访问，而是由语言或框架本身在后台自动处理同步和并发控制。
2. 非公平锁, 不保证锁按照请求锁的顺序来获得锁, 在非公平锁的情况下，线程可能会“插队”获取锁，即使有其他线程已经在等待锁。
3. 悲观锁, 对共享变量的变化的预期总是悲观的
4. 独占锁, 同一时刻只有一个线程抢到锁
5. 互斥锁, 同一时刻只能有一个加锁的线程执行代码
6. 可重入锁, 同一线程在抢到锁后, 仍然可以继续参与抢锁

通过上述特点可以得出, synchronized锁效率低下

![image-20241220171340399](https://raw.githubusercontent.com/luobai0110/blogpic/main/image-20241220171340399.png)

#### synchronized 修饰代码块, 显示锁

```java
@Getter
public class Account {
    private BigDecimal balance = BigDecimal.ZERO;
    private final Object LOCK = new Object();
    public void deposit(double money) {
        synchronized (LOCK) {
            balance = balance.add(BigDecimal.valueOf(money));
        }
        System.out.println(Thread.currentThread().getName() + "balance:" + balance);
    }
}
```

![image-20241220171129750](https://raw.githubusercontent.com/luobai0110/blogpic/main/image-20241220171129750.png)



#### synchronized的缺点



### ReetrantLock

优点: 更加细腻

如何使用

```java
Lock l = ...;
l.lock();
try {
    
} finally {
   l.unlock();
}
```

```java
@Getter
public class Account {
    private final ReentrantLock rlock = new ReentrantLock();
    private BigDecimal balance = BigDecimal.ZERO;


    public void deposit(double money) {
        rlock.lock();
        try {
            balance = balance.add(BigDecimal.valueOf(money));
        } finally {
            rlock.unlock();
        }

        System.out.println(Thread.currentThread().getName() + "balance:" + balance);
    }
}
```

![](https://raw.githubusercontent.com/luobai0110/blogpic/main/image-20241220172342113.png)


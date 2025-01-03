---
title: java多线程
date: 2024-12-20 11:02:54
category: 
  - java
tag:
  - java
---

## 待办列表

- [ ]  java中的常见锁
- [x]  synchronized的使用
- [ ]  了解threadFactory

## 多线程的应用场景

1. 大量数据需要处理
2. 程序需要异步执行

## 进程与线程的区别

- 进程: 进程是操作系统进行资源分配和调度的最小单元，可以简单地理解为系统中运行的一个程序就是一个进程。
- 线程: cpu能够调度的最小单元, 进程中的一个个执行流程。

## java的多线程

### 调用run方法和调用start方法的区别

- 调用start的方法会创建一个新的线程, 然后os会调用run方法
- 调用run方法只是普通的调用方法, 并不会创建一个新的线程

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

### 创建带返回值的多线程

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

输出3所需时间: **至少**三秒

## synchronized

此段输出执行代码如下: 

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

### 使用场景

`synchronozed`适用于简单并发场景, 尤其是对性能要求不高的场景

### **`synchronozed`**的特点

1. **隐式锁**, 指的是在编程语言或框架中，不需要显式地使用锁（如互斥锁、读写锁等）来控制对共享资源的访问，而是由语言或框架本身在后台自动处理同步和并发控制。
2. **非公平锁**, 不保证锁按照请求锁的顺序来获得锁, 在非公平锁的情况下，线程可能会“插队”获取锁，即使有其他线程已经在等待锁。
3. **悲观锁**, 对共享变量的变化的预期总是悲观的
4. **独占锁**, 同一时刻只有一个线程抢到锁
5. **互斥锁,** 同一时刻只能有一个加锁的线程执行代码
6. **可重入锁**, 同一线程在抢到锁后, 仍然可以继续参与抢锁
7. **粒度**: 
   - **方法级别**：锁定整个方法。
   - **代码块级别**：锁定特定的代码块，粒度更细，性能更好。

### sysnchronzied锁的粒度

#### 实例方法上的synchronized

```java
public synchronized void deposit(double money) {
    balance = balance.add(BigDecimal.valueOf(money));
    System.out.println(Thread.currentThread().getName() + "balance:" + balance);
}
```

当synchronized修饰的实例方法时, 他锁定的是**当前实例**;

注意: 如果不同的线程正在访问同一个对象实例的**不同同步实例方法**，它们会互相阻塞，因为它们都竞争同一个锁。

通过上述特点可以得出, synchronized锁效率低下

![输出效果](https://raw.githubusercontent.com/luobai0110/blogpic/main/image-20241220171340399.png)

#### 代码块上的 synchronized

在这种情况下，需要指定一个对象作为锁。通常，这个对象可以是实例变量、类变量或是一个新创建的对象。

优点: 提供了灵活性, 允许一个类的不同代码块使用不同的锁, 能够更加细腻的控制并发编程

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

![输出效果](https://raw.githubusercontent.com/luobai0110/blogpic/main/image-20241220171129750.png)

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

## ThreadPoolExecutor

参数详解:


1. 核心线程数量: 线程池中始终保持的线程数量，即使这些线程处于空闲状态。(注意, 此处线程仍然是在提交任务时创建)
    线程创建数量:

    - 
      内存(IO)密集型任务: 核数 * 2

    - 
      实际情况会根据压力测试指定

    - 
      CPU密集型任务: 核数 + 1

2. 最大线程数量: 线程池中允许的最大线程数量。当任务数量超过核心线程数且任务队列已满时，线程池会创建新的线程，直到达到最大线程数。

    - 一般数量: 核心 * 2
    - 非核心创建时机: 核心线程都在工作且任务队列已满时, 创建非核心线程
    - 非核心: 超时会销毁

3. 空闲时间: 非核心线程不处理任务的时间, 当线程池中的线程数量超过核心线程数时，多余的线程在空闲时间超过keepAliveTime后会被终止。

4. 空闲时间单位:

5. 任务队列: 储存任务的队列

    - 有界队列: ArrayBlockingQueue
    - 无界队列: LinkedBlockingQueue
    - 如果使用有界队列, 池中最多同时存在任务数量: 有界队列大小加上最大线程数

6. 线程工厂:

7. 拒绝策略:

    - `AbortPolicy`:这是默认的策略。当任务被拒绝时，它会抛出 `RejectedExecutionException` 异常。这是一种简单的策略，但它可能会打断调用者的正常工作流程。
    - `CallerRunsPolicy`：这个策略不会抛出异常，而是将任务退回到调用者那里，由调用者的线程来执行这个任务。这种方式可以减轻线程池的负担，但可能会降低调用者的响应性。
    - `DiscardPolicy`：这个策略默默地丢弃被拒绝的任务，不会抛出异常，也不会执行任务。这种策略适用于那些可以丢弃的任务，比如一些后台日志收集任务。
    - `DiscardOldestPolicy`：这个策略会丢弃线程池中最老的任务，然后尝试再次提交新任务。这种方式在任务优先级不高的情况下可能很有用，但它同样会丢失任务。
    
    此外还可以通过实现`RejectedExecutionHandler`接口来自定义决绝策略
    
    触发拒绝策略的时机: 超过池中最大同时存在的任务数量

执行流程:

![image-20241221150601130](https://raw.githubusercontent.com/luobai0110/blogpic/main/image-20241221150601130.png)

## stream流与多线程

使用`parallel`开启并行流, 注意只有当数据足够大时, 开启并行流才有意义

1. 数据量较小时: 

    ```java
    public class Test {
        public static void main(String[] args) {
            LongStream lsA = LongStream.rangeClosed(1, 1000L);
            long startA = System.currentTimeMillis();
            long sumA = lsA.parallel().sum();
            long endA = System.currentTimeMillis();
            System.out.println(endA - startA);
    
    
            LongStream lsB = LongStream.rangeClosed(1, 1000L);
            long startB = System.currentTimeMillis();
            long sumB = lsB.sum();
            long endB = System.currentTimeMillis();
            System.out.println(endB - startB);
    
            System.out.println("A:\t" + sumA + "\n" + "B:\t" + sumB);
    
        }
    }
    ```

![image-20241221152943791](https://raw.githubusercontent.com/luobai0110/blogpic/main/image-20241221152943791.png)

   非并发的方式耗时小于并发, 这是因为数据量小, 线程创建的花销大于计算的花销

2. 大量数据时:

   ```java
   public class Test {
       public static void main(String[] args) {
           LongStream lsA = LongStream.rangeClosed(1, 100000000000L);
           long startA = System.currentTimeMillis();
           long sumA = lsA.parallel().sum();
           long endA = System.currentTimeMillis();
           System.out.println(endA - startA);
   
   
           LongStream lsB = LongStream.rangeClosed(1, 100000000000L);
           long startB = System.currentTimeMillis();
           long sumB = lsB.sum();
           long endB = System.currentTimeMillis();
           System.out.println(endB - startB);
   
           System.out.println("A:\t" + sumA + "\n" + "B:\t" + sumB);
   
       }
   }
   ```
   
   

![image-20241221153751144](https://raw.githubusercontent.com/luobai0110/blogpic/main/image-20241221153751144.png)

## JDK中线程安全的类

JUC包(并发安全包)

线程安全问题:

1. 单个数据
   - 线程不安全:
     - 单个数据: 八种基本数据类型
     - 包装类: 四类八种
     - 大类(为解决基本数据类型范围和浮点数精度问题引入): BigDecimal, BigInteger
   - 线程安全:
     - 原子类, 以Atomic开头的类, AtomicInteger, AtomicLong

2. 多个数据:
   - 线程不安全:
     - 单列集合: ArrayList, LinkedList, HashSet, TreeSet
   - 线程安全:
     - 单列集合: CopyOnWriteArrayList, CopyOnWriteArraySet(只有修改才加锁), Vector(读写操作都加锁)
     - 双列集合: ConCurrentHashMap

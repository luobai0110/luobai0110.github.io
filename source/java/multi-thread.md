---
title: java多线程
date: 2024-12-20 11:02:54
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

线程之间共享堆区, 不共享栈区, 目的是多线程之间处理任务不相互影响

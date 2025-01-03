---
title: 设计模式
date: 2024-12-20 17:48:43
category: 
  - 计算机基础
tag:
  - cs
---

# 设计模式

## 装饰器模式

### 目的

可以在不修改要增强的类的基础上灵活增强一个类的功能, 是可插拔的.

装饰模式以对客户透明的方式动态地给一个对象附加上更多的责任.

换言之，客户端并不会觉得对象在装饰前和装饰后有什么不同。装饰模式可以在不需要创造更多子类的情况下，将对象的功能加以扩展。

### 策略模式是什么

动态地给一个对象增加一些额外的职责(Responsibility)

装饰模式比生成子类实现更为灵活

### 优缺点

#### 优点

- 装饰模式与继承关系的目的都是要扩展对象的功能，但是装饰模式可以提供比继承更多的灵活性。
- 可以通过一种动态的方式来扩展一个对象的功能，通过配置文件可以在运行时选择不同的装饰器，从而实现不同的行为。
- 通过使用不同的具体装饰类以及这些装饰类的排列组合，可以创造出很多不同行为的组合。可以使用多个具体装饰类来装饰同一对象，得到功能更为强大的对象。
- 具体构件类与具体装饰类可以独立变化，用户可以根据需要增加新的具体构件类和具体装饰类，在使用时再对其进行组合，原有代码无须改变，符合“开闭原则”

#### 缺点

- 使用装饰模式进行系统设计时将产生很多小对象，这些对象的区别在于它们之间相互连接的方式有所不同，而不是它们的类或者属性值有所不同，同时还将产生很多具体装饰类。这些装饰类和小对象的产生将增加系统的复杂度，加大学习与理解的难度。
- 这种比继承更加灵活机动的特性，也同时意味着装饰模式比继承更加易于出错，排错也很困难，对于多次装饰的对象，调试时寻找错误可能需要逐级排查，较为烦琐。

### 实现步骤:

1. 被装饰类与装饰器类应当具备相同的父类;
2. 装饰器类组合父类
3. 给装饰器类提供有参构造器, 构造器是组合的父类属性
4. 重写父类方法

## 单例设计模式(Singleton)

### 目的

保证一个类在进程中有且只有一个实例

### 关键步骤

1. 构造器私有化, 无法从外部创建对象
2. 提供一个静态的该类成员变量, 确保该类的实例在内存中只存在一份
3. 提供一个静态的方法获取静态实例

### 实现方法

#### 1. 饿汉模式

- **特点: **在声明静态对象是直接实例化
- 优点:
  - **线程安全**, 在类加载是就实例化对象, 天生线程安全
  - **简单容易实现**
  - **性能较高**: 第一次获取时不需要实例化对象
- 缺点:
  - **资源浪费**: 如果单例对象在应用程序的整个生命周期中从未被使用过，那么它的创建和初始化就是一种资源浪费。
  - **不支持延迟加载**：实例在类加载时就被创建，无法实现按需加载（即延迟加载），这在某些场景下可能是不必要的。
  - **类加载时就初始化**：如果单例对象的初始化过程比较复杂或耗时，可能会影响应用程序的启动时间

实现代码如下

```java
public class Admin {
    private String name;
    private String password;
    private Admin() {
    }
	//  饿汉单例, 调用方法前对象就已经创建
    private static final Admin admin = new Admin();
    public static Admin getInstance() {
        return admin;
    }
}
```

#### 2. 懒汉模式

- **特点**: 在第一次请求时才会创建实例
- 优点:
  - **延迟加载**: 只有调用方法是对象才会被实例化
  - 如果单例对象在整个应用程序生命周期中从未被使用，那么它的创建和初始化过程就不会发生.
- 缺点: 线程不安全,  如果加锁则会导致性能问题

实现代码如下

```java
public class Admin {
    private String name;
    private String password;
    private Admin() {
    }
//     懒汉单例
    private static Admin admin;
    // 需要对整个方法进行加锁
    public synchronized static Admin getInstance() {
        if (Objects.isNull(admin)) {
            admin = new Admin();
        }
        return admin;
    }
}
```

#### 3. 双重懒汉

- **特点** : 普通懒汉的线程优化版本, 避免每次获得单例时都要加锁, 提高性能

实现代码如下

```java
public class Admin {
    private String name;
    private String password;
    private Admin() {}
    private static volatile Admin admin;
    public static Admin getInstance() {
        if (admin == null) {
            // 同步代码块确保只有一个线程获得锁
            synchronized (Admin.class) {
                // 第二次判空, 避免第一次判断时有其他线程通过了检查, 保证只有一个线程能够创建实例
                if (admin == null) admin = new Admin();
            }
        }
        return admin;	
    }
}
```

#### 4. 静态内部类实现

优点:

1. **延迟加载（懒汉式）**：
   - 由于 `INSTANCE` 是在 `AdminInstance` 类首次被加载时初始化的，因此只有在真正需要时才会创建实例，避免了在类加载时就创建实例的浪费，符合懒加载的特性。

2. **不会加锁**：
   - 不像传统的双重检查锁定或同步方法，这种实现不会在每次调用 `getInstance()` 时加锁，因此具有更高的性能。

3. **类加载机制保证唯一性**：
   - JVM 的类加载机制保证了一个类只会被加载一次，因此 `INSTANCE` 也只会被创建一次，并且在多线程环境下不会出现竞争条件。

实现代码

```java
public class Admin {
    private String name;
    private String password;
    private Admin() {}
    // 静态内部类，内部类的静态变量 INSTANCE 保存了单例对象, 只有访问该类时才会被加载
    private static class AdminInstance{
        // 通过 JVM 的类加载机制，确保 INSTANCE 只会在第一次被访问时创建
        private static final Admin INSTANCE = new Admin();
    }
    public static Admin getInstance() {
        return AdminInstance.INSTANCE;
    }
}
```

静态内部类的解释：

- 静态内部类 `AdminInstance` 是 `Admin` 类的一部分，它只有在 `getInstance()` 方法调用时才会被加载。
- 当 `getInstance()` 方法被调用时，JVM 会检查 `AdminInstance` 类是否已经加载，如果没有加载，JVM 会加载它，并在加载时初始化 `INSTANCE`。
- 一旦类被加载，它会保持在内存中，后续对 `getInstance()` 的调用不再导致 `AdminInstance` 类的重新加载。

#### 5. 通过枚举实现

**实现原理**

- 枚举类型在 JVM 中是由 Enum 类继承的，JVM 在加载枚举时会确保它们是唯一的，并且会自动为枚举实例提供线程安全的支持。
- 枚举的实例是在类加载时就创建的，而且 JVM 保证枚举实例在整个程序生命周期内是唯一的，不会被多次实例化。
- 枚举还会自动防止通过反射或反序列化来重新创建单例实例。

实现代码如下:

```java
public enum Admin {
    INSTANCE;
    private String name;
    private String password;
    private Admin() {}
    public String getPassword() {
        return password;
    }
    public void setAdminInfo(String name, String password) {
        this.name = name;
        this.password = password;
    }
    public void setPassword(String password) {
        this.password = password;
    }
    public String getName() {
        return name;
    }
    public void setName(String name) {
        this.name = name;
    }
}
```

参考连接:

> [Java并发编程：volatile关键字解析](https://www.cnblogs.com/dolphin0520/p/3920373.html)
>
> [Java单例模式的7种写法中，为何用Enum枚举实现被认为是最好的方式？【享学Java】](https://cloud.tencent.com/developer/article/1497592)
>
> [静态内部类何时初始化](https://www.cnblogs.com/maohuidong/p/7843807.html)



## 策略模式

## 建造者模式

### 建造者模式是什么

将一个复杂对象的构建与它的表示分离，使得同样的构建过程可以创建不同的表示。

建造者模式是一步一步创建一个复杂的对象，它允许用户只通过指定复杂对象的类型和内容就可以构建它们，用户不需要知道内部的具体构建细节。建造者模式属于对象创建型模式。

![16cf110c95a2fd81~tplv-t2oaga2asx-jj-mark_3024_0_0_0_q75](https://raw.githubusercontent.com/luobai0110/blogpic/main/16cf110c95a2fd81%7Etplv-t2oaga2asx-jj-mark_3024_0_0_0_q75.png)

### 四种角色

- Product： 是最终生成的对象。 由不同生成器构造的产品无需属于同一类层次结构或接口。
- Builder**抽象建造者**：, 接口声明在所有类型生成器中通用的产品构造步骤。
- ConcreteBuilder**具体建造者**：提供构造过程的不同实现。 具体生成器也可以构造不遵循通用接口的产品。
- Director**指挥者**：类定义调用构造步骤的顺序， 这样你就可以创建和复用特定的产品配置。



### 使用场景

- 使用生成器模式可避免 “重叠构造函数 （telescoping constructor）” 的出现
- 当你希望使用代码创建不同形式的产品
- 使用生成器构造组合树或其他复杂对象。



![家装建造者模式简单的 UML 图](https://p1-jj.byteimg.com/tos-cn-i-t2oaga2asx/gold-user-assets/2019/9/2/16cf1253f22376f3~tplv-t2oaga2asx-jj-mark:3024:0:0:0:q75.png)

### 静态内部类实现

- 在要构建的类内部创建一个静态内部类 Builder
- 静态内部类的参数与构建类一致
- 构建类的构造参数是 静态内部类，使用静态内部类的变量一一赋值给构建类
- 静态内部类提供参数的 setter 方法，并且返回值是当前 Builder 对象
- 最终提供一个 build 方法构建一个构建类的对象，参数是当前 Builder 对象

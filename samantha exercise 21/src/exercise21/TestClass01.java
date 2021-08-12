package exercise21;

import org.testng.annotations.Test;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.AfterMethod;

public class TestClass01 {
  @Test(priority=2)
  public void tMethod1() {
	  System.out.println("method 01");
  }
  @Test(priority=1)
  public void tMethod2() {
	  System.out.println("method 02");
  }
  @Test(priority=3)
  public void tMethod5() {
	  System.out.println("method 5");
  }
  @BeforeMethod
  public void beforeMethod() {
  }

  @AfterMethod
  public void afterMethod() {
  }

}
